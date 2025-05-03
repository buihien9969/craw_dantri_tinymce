<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        if (!Schema::hasTable('edit_requests')) {
            Schema::create('edit_requests', function (Blueprint $table) {
                $table->id();
                $table->foreignId('article_id')->constrained('articles', 'article_id')->onDelete('cascade');
                $table->foreignId('user_id')->constrained('users', 'user_id')->onDelete('cascade');
                $table->text('reason');
                $table->enum('status', ['pending', 'approved', 'rejected'])->default('pending');
                $table->text('rejection_reason')->nullable();
                $table->timestamp('approved_at')->nullable();
                $table->timestamp('rejected_at')->nullable();
                $table->timestamps();
            });
        }
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('edit_requests');
    }
};
