<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('approvals', function (Blueprint $table) {
            $table->id('approval_id');
            $table->string('type')->default('role_upgrade');
            $table->foreignId('article_id')->nullable()->constrained('articles', 'article_id')->onDelete('cascade');
            $table->foreignId('user_id')->constrained('users', 'user_id')->onDelete('cascade');
            $table->foreignId('approved_by')->nullable()->constrained('users', 'user_id')->onDelete('set null');
            $table->string('cccd_number')->nullable();
            $table->string('cccd_front')->nullable();
            $table->string('cccd_back')->nullable();
            $table->json('certificates')->nullable();
            $table->string('requested_role')->nullable();
            $table->enum('status', ['pending', 'approved', 'rejected'])->default('pending');
            $table->text('reject_reason')->nullable();
            $table->text('remarks')->nullable();
            $table->timestamp('processed_at')->nullable();
            $table->foreignId('processed_by')->nullable()->constrained('users', 'user_id')->onDelete('set null');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('approvals');
    }
};
